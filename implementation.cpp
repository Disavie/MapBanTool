#include "header.hpp"


using std::cout, std::cin, std::getline, std::string;

std::string getVal(std::string const & s){
	return s.substr(s.find('=')+1, s.size() - s.find('=') + 1);
}

std::vector<string> getInput(std::ifstream & s){
    string input;
    std::vector<string> output;
    while(getline(s,input)){	
        output.push_back(input);
    }
    return output;
}

std::vector<std::string>::iterator filterInput(std::vector<std::string> & vec, std::string const & key){
    if(key == "*") return vec.end();
    auto it = std::remove_if(vec.begin(),vec.end(),[&](auto s){
                                            return (s.find(key) == std::string::npos);
                                            });
    return it;        
}


void countPickBan(std::vector<std::string> const & list, std::vector<std::tuple<std::string,int,int>> & maps){
    std::for_each(maps.begin(),maps.end(),[&](auto & x){
                    std::string map = std::get<0>(x);
                    int pickcount = 0;
                    int bancount = 0;
                    std::for_each(list.begin(),list.end(),[&](auto line){
                                    if(line.find("picked by") != std::string::npos && line.find(map) != std::string::npos){
                                        //std::cout << "incremented counter for " << map << std::endl;
                                        pickcount++;
                                    }
                                    });
                    std::for_each(list.begin(),list.end(),[&](auto line){
                                    if(line.find("banned") != std::string::npos && line.find(map) != std::string::npos){
                                        //std::cout << "incremented counter for " << map << std::endl;
                                        bancount++;
                                    }
                                    });
                    std::get<1>(x) = pickcount;
                    std::get<2>(x) = bancount;
                    });
}