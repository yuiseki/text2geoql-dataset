[out:json][timeout:30000];
area["name:en"="South Korea"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Seoul"](area.searchArea);
);
out geom;
