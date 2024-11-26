#include "header.hpp"

int main(){
	
	std::fstream fs;
	fs.open("config.txt");
	std::string from_config;
	fs >> from_config;
	int width = std::stoi(getVal(from_config));
	
	//int width = 0;
	
	
	
    std::string key;
    std::ofstream output_file_stream;

    std::vector<std::tuple<std::string,int,int>> map_data =
{{"Busan",0,0},{"Ilios",0,0},{"Oasis",0,0},
{"Hollywood",0,0}, {"King's Row",0,0}, {"Midtown",0,0},
{"Colosseo",0,0}, {"Esperança",0,0}, {"Runasapi",0,0},
{"New Junk City",0,0},{"Suravasa",0,0}, {"Hanaoka",0,0}, {"Throne of Anubis",0,0},
{"Circuit Royal",0,0}, {"Watchpoint Gibraltar",0,0}, {"Shambali Monastery",0,0}};

//3 KOTH MAPS
//3 HYBRID
//3 PUSH MAPS
//4 CLASH FLASHPOINT MAPS
//3 PAYLOAD MAPS

	std::cout << "Enter team to aggregate mapban data : " ;
    while(getline(std::cin,key)){
		if(key.empty()) break;
		std::ifstream input_file_stream("data.txt");
		std::vector<std::string> list = getInput(input_file_stream);
		auto end_it = filterInput(list,key);
		list.erase(end_it,list.end());
		countPickBan(list,map_data);
		
		//FORMATTING OUTPUT
		output_file_stream.open("output_files/"+key+".txt");
		output_file_stream << std::left  << std::setw(width)<< "map" << '\t'
							<< std::left << std::setw(width) <<"#picked" << '\t'
							<< std::left << std::setw(width) <<"#banned" << std::endl; 
		std::for_each(map_data.begin(),map_data.end(),[&](auto x){
									output_file_stream << std::left << std::setw(width) <<std::get<0>(x)  << '\t'
														<< std::left << std::setw(width) << std::get<1>(x) << '\t'
														<< std::left << std::setw(width) << std::get<2>(x) << std::endl;   
									});
		output_file_stream << " * data from 10/08-11/26 " << std::endl;
		output_file_stream.close();
		
		output_file_stream.open("output_files/raw.txt");
		std::for_each(list.begin(),end_it,[&](auto x){output_file_stream << x << '\n';});
		output_file_stream.close();
		std::cout << "Enter team to aggregate mapban data : " ;
	}
    return 0;
}