[out:json][timeout:30];
area["name:en"="Oslo"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;