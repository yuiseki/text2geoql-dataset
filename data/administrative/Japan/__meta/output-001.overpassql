[out:json][timeout:30000];
area["name:en"="Japan"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=4](area.searchArea);
);
out meta;
