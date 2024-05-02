[out:json][timeout:30000];
area["name:en"="New York State"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="New York"](area.searchArea);
);
out geom;
