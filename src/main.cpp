#include "header.hpp"
#include "map_info.hpp"


int main(){
	
	std::ifstream fs;
	fs.open("src/config.txt");
	std::string from_config;

	std::getline(fs,from_config);

	std::vector<std::string> key = parseHelper(getVal(from_config));
	fs >> from_config;
	int width = std::stoi(getVal(from_config));
	fs.close();

	fs.open("mappool.txt");
	std::vector<std::string> maps = getInput(fs);
	fs.close();

	//create map pools
	fs.open("src/cache/winrates.cache");
	nlohmann::json jsonData;
	fs >> jsonData;
	fs.close(); 

	std::vector<map_info> map_pool;
	for(std::string map : maps){
		map_info temp;
		temp.name = map;
		temp.timesBanned=0;
		temp.timesPicked = 0;
		for (auto& [key, value] : jsonData.items()) {
			//std::cout << key << ' ' << map << std::endl;
        	if (map == key) {
				//std::cout << key << ' ' << value[0] << ' ' << value[1] << std::endl;
				std::string s = nlohmann::to_string(value[0]);
				s.erase(remove( s.begin(), s.end(), '\"' ),s.end());
            	temp.winrate = std::stoi(s);

				s = nlohmann::to_string(value[1]);
				s.erase(remove( s.begin(), s.end(), '\"' ),s.end());
				temp.timesPlayed = std::stoi(s);
        	}
    	}
		map_pool.push_back(temp);
	}


	
	
    std::ofstream output_file_stream;
	std::ifstream input_file_stream("src/cache/temp.cache");
	std::vector<std::string> list = getInput(input_file_stream);
	auto end_it = filterInput(list,key);
	list.erase(end_it,list.end());
	countPickBan(list,map_pool);
	std::cout << "{MapBanTool}\tHow do you want to sort output?\n" <<
				"{MapBanTool}\tType 'w' to sort by win%, 'b' to sort by #banned, 'p' to sort by #picked\n" <<
				"{MapBanTool}\t>>> ";
	char mode;
	std::cin >> mode;

	sort_data(map_pool,mode);
		
	//FORMATTING OUTPUT
	output_file_stream.open("output_files/"+key[0]+".txt");
	output_file_stream << std::left  << std::setw(width)<< "map" << '\t'
						<< std::left << std::setw(width) <<"#picked" << '\t'
						<< std::left << std::setw(width) <<"#banned" << '\t'
						<< std::left << std::setw(width) <<"win%" << '\t'
						<< std::left << std::setw(width) <<"#played" << std::endl; 
	std::for_each(map_pool.begin(),map_pool.end(),[&](auto x){
									output_file_stream << std::left << std::setw(width) <<x.name  << '\t'
														<< std::left << std::setw(width) << x.timesPicked << '\t'
														<< std::left << std::setw(width) << x.timesBanned << '\t'
														<< std::left << std::setw(width) << std::to_string(x.winrate)+" %" <<'\t'
														<< std::left << std::setw(width) << x.timesPlayed << std::endl;

							});
	output_file_stream.close();
	
	output_file_stream.open("output_files/raw.txt");
	std::for_each(list.begin(),list.end(),[&](auto x){output_file_stream << x << '\n';});
	output_file_stream.close();

    return 0;
}