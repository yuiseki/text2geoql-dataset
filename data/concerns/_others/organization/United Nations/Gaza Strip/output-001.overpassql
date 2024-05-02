[out:json][timeout:30000];
area["name:en"="Gaza Strip"]->.searchArea;
(
  nwr["name"~"UN"](area.searchArea);
  nwr["name:en"~"UN"](area.searchArea);
);
out geom;
