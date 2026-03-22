[out:json][timeout:30];
area["name:en"="Bucharest"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;