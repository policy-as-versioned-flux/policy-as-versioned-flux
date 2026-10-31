// Copyright 2026 Policy as Versioned Flux contributors.
// SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only
#ifndef TWIN_ORIGIN_H
#define TWIN_ORIGIN_H
#include <stdint.h>
#include <map>
#include <string>
#include <vector>

// Plain data copied with Xpdf's existing word/line arrays. item0 is ineligible.
struct TwinOriginRef { uint64_t item; unsigned scalar; unsigned generated; };

class TwinSha256 {
public:
  TwinSha256();
  void update(const char *bytes, size_t length);
  std::string hex() const;
private:
  void block(const unsigned char *bytes);
  uint32_t state[8];
  unsigned char pending[64];
  uint64_t count;
  size_t used;
};

// One owned invocation; no global ledger or authority flag. This records raw tool
// facts only. Actual run identity/wait/EOF/cleanup belongs to the host observer.
class TwinOrigin {
public:
  explicit TwinOrigin(int fd);
  void page(unsigned number);
  void begin(const char *codes, size_t length);
  void end();
  uint64_t decode(int codeBytes, const unsigned *input, int inputLength,
                  const unsigned *mapped, int mappedLength,
                  bool replacement = false, bool actualText = false);
  void emit(TwinOriginRef ref, const char *bytes, int length, bool mirror = false);
  void generated(const char *bytes, int length, const char *reason);
  void finish();
private:
  struct Item {
    uint64_t fragment, start, end;
    std::vector<unsigned> scalars;
    std::vector<bool> used;
    std::string taint;
  };
  typedef std::map<std::string, std::string> Fields;
  void event(Fields fields);
  void line(const Fields &fields, bool prefix);
  void emitted(TwinOriginRef ref, const char *bytes, int length,
               const std::string &operation, const std::string &reason);
  void barrier(const std::string &reason);
  static std::string quote(const std::string &text);
  static std::string hex(const char *bytes, size_t length);
  static std::string scalars(const unsigned *values, int length);
  int fd;
  uint64_t wireBytes, eventCount, outputBytes, fragmentCount, closedCount;
  unsigned pageNumber;
  uint64_t activeFragment, codeCursor;
  std::string codes;
  std::vector<Item> items;
  TwinOriginRef previous;
  TwinSha256 prefixHash, outputHash;
  bool finished;
};
#endif
