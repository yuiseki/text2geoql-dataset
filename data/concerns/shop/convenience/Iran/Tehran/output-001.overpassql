[out:json][timeout:30];
area["name:en"="Tehran"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;