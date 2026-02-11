#include <cctype>

extern "C" {

bool valid_name(const char* name) {
    if (!name) return false;
    for (int i = 0; name[i]; i++) {
        if (!isalnum(name[i]) && name[i] != '-' && name[i] != '_')
            return false;
    }
    return true;
}

unsigned int hash_name(const char* name) {
    unsigned int hash = 5381;
    int c;
    while ((c = *name++))
        hash = ((hash << 5) + hash) + c;
    return hash;
}

}
