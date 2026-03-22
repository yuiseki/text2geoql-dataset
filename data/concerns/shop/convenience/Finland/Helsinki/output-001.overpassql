[out:json][timeout:30];
area["name:en"="Helsinki"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;