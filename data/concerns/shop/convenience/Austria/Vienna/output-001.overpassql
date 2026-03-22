[out:json][timeout:30];
area["name:en"="Vienna"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;