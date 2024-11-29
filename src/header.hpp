#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <algorithm>
#include <tuple>
#include <iomanip>
#include "map_info.hpp"
#include "nlohmann/json.hpp"



std::string getVal(std::string const & s);
std::vector<std::string> parseHelper(const std::string& input);
std::vector<std::string> getInput(std::ifstream & s);
std::vector<std::string>::iterator filterInput(std::vector<std::string> & vec, std::vector<std::string >const & key);
void countPickBan(std::vector<std::string> const & list, std::vector<map_info> & maps);
void sort_data(std::vector<map_info> & map_pool,char c);
