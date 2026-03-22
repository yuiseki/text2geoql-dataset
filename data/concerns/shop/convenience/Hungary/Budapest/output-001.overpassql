[out:json][timeout:30];
area["name:en"="Budapest"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;