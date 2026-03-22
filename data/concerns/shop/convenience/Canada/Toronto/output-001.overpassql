[out:json][timeout:30];
area["name:en"="Toronto"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;