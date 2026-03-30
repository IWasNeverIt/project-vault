#include <algorithm>
#include <cctype>
#include <cstring>
#include <vector>

extern "C" {

bool valid_name(const char* name) {
    if (!name || name[0] == '\0') return false;
    for (int i = 0; name[i]; i++) {
        if (i >= 64) return false;
        if (!isalnum(name[i]) && name[i] != '-' && name[i] != '_')
            return false;
    }
    return true;
}

unsigned int levenshtein(const char* a, const char* b) {
    int la = (int)strlen(a), lb = (int)strlen(b);
    std::vector<unsigned int> prev(lb + 1), curr(lb + 1);
    for (int j = 0; j <= lb; j++) prev[j] = j;
    for (int i = 1; i <= la; i++) {
        curr[0] = i;
        for (int j = 1; j <= lb; j++) {
            if (a[i - 1] == b[j - 1])
                curr[j] = prev[j - 1];
            else
                curr[j] = 1 + std::min({prev[j], curr[j - 1], prev[j - 1]});
        }
        std::swap(prev, curr);
    }
    return prev[lb];
}

}
