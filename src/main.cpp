#include "header.hpp"

int main(){
	
	std::ifstream fs;
	fs.open("src/config.txt");
	std::string from_config;
	std::getline(fs,from_config);
	std::string key = getVal(from_config);
	fs >> from_config;
	int width = std::stoi(getVal(from_config));
	fs.close();

	fs.open("mappool.txt");
	std::vector<std::string> map_pool = getInput(fs);
	fs.close();
	
	//int width = 0;
	
	
    std::ofstream output_file_stream;

    std::vector<std::tuple<std::string,int,int>> map_data =
{{"Busan",0,0},{"Ilios",0,0},{"Oasis",0,0},{"Antarctic Peninsula",0,0},{"Lijiang Tower",0,0 },{"Nepal",0,0},{"Samoa",0,0},
{"Hollywood",0,0}, {"King's Row",0,0}, {"Midtown",0,0},{"Blizzard World",0,0},{"Eichenwalde",0,0},{"Numbani",0,0},{"Parasxo",0,0},
{"Colosseo",0,0}, {"Esperanxa",0,0}, {"Runasapi",0,0},{"New Queen Street",0,0},
{"New Junk City",0,0},{"Suravasa",0,0}, {"Hanaoka",0,0}, {"Throne of Anubis",0,0},
{"Circuit Royal",0,0}, {"Watchpoint Gibraltar",0,0}, {"Shambali Monastery",0,0},{"Dorado",0,0},{"Havana",0,0},{"Junkertown",0,0},{"Route 66",0,0},{"Rialto",0,0}};

//3 KOTH MAPS
//3 HYBRID
//3 PUSH MAPS
//4 CLASH FLASHPOINT MAPS
//3 PAYLOAD MAPS

	std::ifstream input_file_stream("src/cache/temp.cache");
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

								if(std::find(map_pool.begin(),map_pool.end(),std::get<0>(x)) != map_pool.end()){
									output_file_stream << std::left << std::setw(width) <<std::get<0>(x)  << '\t'
														<< std::left << std::setw(width) << std::get<1>(x) << '\t'
														<< std::left << std::setw(width) << std::get<2>(x) << std::endl;
								}   
							});
	output_file_stream.close();
	
	output_file_stream.open("output_files/raw.txt");
	std::for_each(list.begin(),end_it,[&](auto x){output_file_stream << x << '\n';});
	output_file_stream.close();

    return 0;
}