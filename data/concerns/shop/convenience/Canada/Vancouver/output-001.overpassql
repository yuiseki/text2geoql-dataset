[out:json][timeout:30];
area["name:en"="Vancouver"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;