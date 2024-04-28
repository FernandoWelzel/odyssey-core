#ifndef MEMORY_H
#define MEMORY_H

#include <map>

class Memory
{
private:
    std::map<int, int> data_map;

public:
    Memory();
    ~Memory();

    int update(int csn, int wen, int address, int data);

    void write(int address, int data);
};

#endif