#pragma once

extern "C" {
    bool valid_name(const char* name);
    unsigned int levenshtein(const char* a, const char* b);
}
