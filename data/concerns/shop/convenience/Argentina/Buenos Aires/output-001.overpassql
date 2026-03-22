[out:json][timeout:30];
area["name:en"="Buenos Aires"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;