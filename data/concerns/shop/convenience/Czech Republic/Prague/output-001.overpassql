[out:json][timeout:30];
area["name:en"="Prague"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;