// Copyright 2026 Policy as Versioned Flux contributors.
// SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only
#include "TwinOrigin.h"
#include <errno.h>
#include <stdexcept>
#include <string.h>
#include <unistd.h>

namespace {
const uint64_t wireLimit = 64ULL * 1024 * 1024;
const uint64_t outputLimit = 128ULL * 1024 * 1024;
const uint64_t eventLimit = 1000000;
uint32_t rotate(uint32_t x, unsigned n) { return (x >> n) | (x << (32 - n)); }
const uint32_t constants[64] = {
  0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
};
void require(bool condition) {
  if (!condition) throw std::runtime_error("pdf-origin-invariant-or-limit");
}
std::string number(uint64_t value) { return std::to_string(value); }
}

TwinSha256::TwinSha256(): count(0), used(0) {
  const uint32_t initial[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                               0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
  memcpy(state, initial, sizeof(state));
}
void TwinSha256::block(const unsigned char *p) {
  uint32_t w[64];
  for (unsigned i=0;i<16;++i) w[i]=(uint32_t(p[4*i])<<24)|(uint32_t(p[4*i+1])<<16)|
      (uint32_t(p[4*i+2])<<8)|uint32_t(p[4*i+3]);
  for (unsigned i=16;i<64;++i) {
    uint32_t a=w[i-15],b=w[i-2];
    w[i]=w[i-16]+(rotate(a,7)^rotate(a,18)^(a>>3))+w[i-7]+(rotate(b,17)^rotate(b,19)^(b>>10));
  }
  uint32_t a=state[0],b=state[1],c=state[2],d=state[3],e=state[4],f=state[5],g=state[6],h=state[7];
  for (unsigned i=0;i<64;++i) {
    uint32_t t1=h+(rotate(e,6)^rotate(e,11)^rotate(e,25))+((e&f)^(~e&g))+constants[i]+w[i];
    uint32_t t2=(rotate(a,2)^rotate(a,13)^rotate(a,22))+((a&b)^(a&c)^(b&c));
    h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;
  }
  state[0]+=a;state[1]+=b;state[2]+=c;state[3]+=d;state[4]+=e;state[5]+=f;state[6]+=g;state[7]+=h;
}
void TwinSha256::update(const char *p, size_t n) {
  count+=n;
  while(n) { size_t take=n<64-used?n:64-used;memcpy(pending+used,p,take);used+=take;p+=take;n-=take;
    if(used==64){block(pending);used=0;}
  }
}
std::string TwinSha256::hex() const {
  TwinSha256 copy=*this;uint64_t bits=count*8;char one=char(0x80),zero=0;
  copy.update(&one,1);while(copy.used!=56)copy.update(&zero,1);
  char tail[8];for(unsigned i=0;i<8;++i)tail[7-i]=char(bits>>(8*i));copy.update(tail,8);
  const char *digits="0123456789abcdef";std::string result;
  for(unsigned i=0;i<8;++i)for(int j=7;j>=0;--j)result+=digits[(copy.state[i]>>(4*j))&15];
  return result;
}
std::string TwinOrigin::quote(const std::string &s) {
  // Protocol strings are fixed ASCII enum/hash/hex values; never arbitrary PDF strings.
  for(size_t i=0;i<s.size();++i)require(s[i]>=32&&s[i]<127&&s[i]!='"'&&s[i]!='\\');
  return "\""+s+"\"";
}
std::string TwinOrigin::hex(const char *p,size_t n) {
  const char *digits="0123456789abcdef";std::string result;result.reserve(2*n);
  for(size_t i=0;i<n;++i){unsigned c=(unsigned char)p[i];result+=digits[c>>4];result+=digits[c&15];}
  return result;
}
std::string TwinOrigin::scalars(const unsigned *p,int n) {
  require(n>=0&&n<=4096&&(n==0||p));std::string result="[";
  for(int i=0;i<n;++i){require(p[i]<=0x10ffff&&!(p[i]>=0xd800&&p[i]<=0xdfff));
    if(i)result+=",";result+=number(p[i]);}
  return result+"]";
}
void TwinOrigin::line(const Fields &fields,bool prefix) {
  std::string raw="{";for(Fields::const_iterator i=fields.begin();i!=fields.end();++i){
    if(i!=fields.begin())raw+=",";raw+=quote(i->first)+":"+i->second;}
  raw+="}\n";require(raw.size()<=65536&&wireBytes+raw.size()<=wireLimit);
  size_t offset=0;while(offset<raw.size()){ssize_t n=write(fd,raw.data()+offset,raw.size()-offset);
    if(n<0&&errno==EINTR)continue;require(n>0);offset+=size_t(n);}
  wireBytes+=raw.size();if(prefix)prefixHash.update(raw.data(),raw.size());
}
void TwinOrigin::event(Fields fields) {
  require(!finished&&eventCount<eventLimit);fields["seq"]=number(eventCount++);line(fields,true);
}
TwinOrigin::TwinOrigin(int fdA): fd(fdA),wireBytes(0),eventCount(0),outputBytes(0),fragmentCount(0),
  closedCount(0),pageNumber(0),activeFragment(0),codeCursor(0),previous{0,0,0},finished(false) {
  require(fd==3);line({{"emitter_protocol_version","1"},{"profile",quote("pdf-text-xpdf-origin/2")},
    {"schema",quote("twin.pdf-output-origin-events/v1")}},true);
}
void TwinOrigin::page(unsigned n) { require(n>0&&!activeFragment);pageNumber=n; }
void TwinOrigin::begin(const char *p,size_t n) {
  require(!activeFragment&&pageNumber&&n<=256ULL*1024*1024);codes.assign(p,n);codeCursor=0;
  activeFragment=++fragmentCount;TwinSha256 hash;hash.update(p,n);
  event({{"code_bytes",number(n)},{"code_sha256",quote(hash.hex())},{"fragment",number(activeFragment)},
    {"page",number(pageNumber)},{"record",quote("fragment_open")}});
}
void TwinOrigin::end() {
  require(activeFragment&&codeCursor==codes.size());event({{"consumed_code_bytes",number(codeCursor)},
    {"fragment",number(activeFragment)},{"record",quote("fragment_close")}});
  ++closedCount;activeFragment=0;codes.clear();codeCursor=0;
}
uint64_t TwinOrigin::decode(int n,const unsigned *input,int inputLength,const unsigned *mapped,
                           int mappedLength,bool replacement,bool actualText) {
  std::string in=scalars(input,inputLength),out=scalars(mapped,mappedLength),codeHex;
  require(replacement||(activeFragment&&n>0&&n<=64&&codeCursor+size_t(n)<=codes.size()));
  uint64_t start=replacement?0:codeCursor,end=replacement?0:codeCursor+n;
  if(!replacement)codeHex=hex(codes.data()+codeCursor,n);
  Item item;item.fragment=replacement?0:activeFragment;item.start=start;item.end=end;
  if(mappedLength)item.scalars.assign(mapped,mapped+mappedLength);item.used.assign(mappedLength,false);
  item.taint=(replacement||actualText)?"actualtext":(in==out?"none":"unicode-remap");
  if(inputLength==0&&!replacement)item.taint="unmapped";
  items.push_back(item);uint64_t id=items.size();
  event({{"code_end",number(end)},{"code_hex",quote(codeHex)},{"code_start",number(start)},
    {"fragment",number(item.fragment)},{"input_scalars",in},{"item",number(id)},
    {"record",quote("item")},{"scalars",out},{"taint",quote(item.taint)}});
  if(!replacement)codeCursor=end;return id;
}
void TwinOrigin::barrier(const std::string &reason) {
  event({{"at",number(outputBytes)},{"reason",quote(reason)},{"record",quote("barrier")}});
}
void TwinOrigin::emitted(TwinOriginRef ref,const char *p,int n,const std::string &op,const std::string &reason) {
  require(n>0&&n<=16&&outputBytes+unsigned(n)<=outputLimit);
  event({{"end",number(outputBytes+n)},{"operation",quote(op)},{"origin_item",number(ref.item)},
    {"origin_scalar",number(ref.scalar)},{"reason",quote(reason)},{"record",quote("emit")},
    {"start",number(outputBytes)},{"utf8_hex",quote(hex(p,n))}});
  outputHash.update(p,n);outputBytes+=n;previous=ref;
}
void TwinOrigin::emit(TwinOriginRef ref,const char *p,int n,bool mirror) {
  if(!n)return;
  if(!ref.item){generated(p,n,ref.generated==1?"spacing":"unmapped");return;}
  require(ref.item<=items.size());Item &item=items[ref.item-1];require(ref.scalar<item.scalars.size());
  bool duplicate=item.used[ref.scalar];std::string op="decoded",reason="source";
  if(duplicate){op="modified";reason="duplicate";}
  else if(mirror){op="modified";reason="mirror";}
  else if(item.taint!="none"){op="modified";reason=item.taint=="actualtext"?"actualtext":
      (item.taint=="unicode-remap"?"remap":"unmapped");}
  if(duplicate)barrier("duplicate");
  else if(previous.item){
    const Item &before=items[previous.item-1];
    if(before.fragment!=item.fragment||!item.fragment)barrier("fragment");
    else if(previous.item==ref.item){if(ref.scalar!=previous.scalar+1)barrier("scalar-order");}
    else if(previous.scalar+1!=before.scalars.size()||ref.scalar!=0)barrier("scalar-order");
    else if(before.end!=item.start)barrier("source-gap");
  }
  item.used[ref.scalar]=true;emitted(ref,p,n,op,reason);
}
void TwinOrigin::generated(const char *p,int n,const char *reason) {
  if(n)emitted({0,0,0},p,n,"generated",reason);
}
void TwinOrigin::finish() {
  require(!finished&&!activeFragment&&fragmentCount==closedCount);
  for(size_t i=0;i<items.size();++i)for(size_t j=0;j<items[i].used.size();++j)if(!items[i].used[j])
    event({{"item",number(i+1)},{"reason",quote("not-emitted-by-reading-order")},
      {"record",quote("omit")},{"scalar",number(j)}});
  Fields footer={{"closed_fragment_count",number(closedCount)},{"emitted_stdout_bytes",number(outputBytes)},
    {"emitted_stdout_sha256",quote(outputHash.hex())},{"event_count",number(eventCount)},
    {"event_prefix_bytes",number(wireBytes)},{"event_prefix_sha256",quote(prefixHash.hex())},
    {"intended_exit_code","0"},{"record",quote("footer")}};
  line(footer,false);finished=true;
}
