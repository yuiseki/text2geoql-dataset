[out:json][timeout:30];
area["name:en"="Kobe"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Chuo Ward"](area.searchArea);
);
out geom;
