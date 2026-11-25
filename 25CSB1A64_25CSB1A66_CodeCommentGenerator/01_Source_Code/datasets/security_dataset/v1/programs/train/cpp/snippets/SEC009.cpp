void load(){ std::string data; std::cin >> data; std::istringstream ss(data); boost::archive::text_iarchive ia(ss); }
