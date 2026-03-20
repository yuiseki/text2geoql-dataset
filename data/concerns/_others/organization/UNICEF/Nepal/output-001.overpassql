[out:json][timeout:30];
area["name:en"="Nepal"]->.searchArea;
(
  nwr["name"~"UNICEF"](area.searchArea);
  nwr["name:en"~"UNICEF"](area.searchArea);
);
out geom;
