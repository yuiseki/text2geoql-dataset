[out:json][timeout:30000];
area["name:en"="Kenya"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Mandera County"](area.searchArea);
);
out geom;
