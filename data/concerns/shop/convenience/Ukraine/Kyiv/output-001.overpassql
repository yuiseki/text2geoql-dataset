[out:json][timeout:30];
area["name:en"="Kyiv"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;