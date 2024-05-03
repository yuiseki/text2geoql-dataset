[out:json][timeout:30000];
area["name:en"="South Korea"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=4](area.searchArea);
);
out meta;
