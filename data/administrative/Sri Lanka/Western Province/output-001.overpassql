[out:json][timeout:30];
area["name:en"="Sri Lanka"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Western Province"](area.searchArea);
);
out geom;
