// TEST_ONLY standalone module exercise. No Xpdf includes/linkage, PDF or authority.
// SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only
#include "TwinOrigin.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <exception>

static void emit(TwinOrigin &origin, uint64_t item, unsigned scalar,
                 const char *bytes, bool mirror=false) {
  origin.emit({item,scalar,0},bytes,int(strlen(bytes)),mirror);
  if(fwrite(bytes,1,strlen(bytes),stdout)!=strlen(bytes))throw 1;
}
static void newline(TwinOrigin &origin) {
  origin.generated("\n",1,"linebreak");
  if(fwrite("\n",1,1,stdout)!=1)throw 1;
}
static uint64_t item(TwinOrigin &origin, unsigned scalar, unsigned mapped=0) {
  unsigned output=mapped?mapped:scalar;return origin.decode(1,&scalar,1,&output,1);
}
int main(int argc,char **argv) {
  // Runner supplies precisely its owned write-pipe FD; it is not an artifact input.
  if(argc!=2)return 90;char *end=NULL;long supplied=strtol(argv[1],&end,10);
  if(!end||*end||supplied<3||supplied>1024)return 90;
  if(supplied!=3){if(dup2(int(supplied),3)!=3)return 90;close(int(supplied));}
  try {
    TwinOrigin origin(3);origin.page(1);
    origin.begin("AB",2);uint64_t a=item(origin,'A'),b=item(origin,'B');origin.end();
    emit(origin,a,0,"A");emit(origin,b,0,"B");newline(origin);
    origin.begin("A-B",3);a=item(origin,'A');item(origin,'-');b=item(origin,'B');origin.end();
    emit(origin,a,0,"A");emit(origin,b,0,"B");newline(origin);
    origin.begin("(",1);a=item(origin,'(');origin.end();
    emit(origin,a,0,")",true);emit(origin,a,0,")",true);newline(origin);
    origin.begin("R",1);a=item(origin,'R','S');origin.end();emit(origin,a,0,"S");newline(origin);
    unsigned x='X';a=origin.decode(0,&x,1,&x,1,true,true);emit(origin,a,0,"X");newline(origin);
    origin.begin("\xe9",1);a=item(origin,0xe9);origin.end();emit(origin,a,0,"\xc3\xa9");newline(origin);
    origin.begin("ab",2);unsigned pair[2]={'a','b'};a=origin.decode(2,pair,2,pair,2);origin.end();
    emit(origin,a,1,"b");emit(origin,a,0,"a");newline(origin);
    origin.begin("Z",1);a=item(origin,'Z');origin.end();emit(origin,a,0,"Z");
    origin.page(2);  // No separator: retain prior source and record a fragment barrier.
    origin.begin("Y",1);a=item(origin,'Y');origin.end();emit(origin,a,0,"Y");newline(origin);
    if(fflush(stdout)||ferror(stdout))return 91;origin.finish();if(close(3))return 92;return 0;
  } catch(const std::exception &error) {fprintf(stderr,"TEST_ONLY recorder failed: %s\n",error.what());return 97;}
  catch(...) {return 98;}
}
