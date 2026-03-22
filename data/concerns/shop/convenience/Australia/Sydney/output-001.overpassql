[out:json][timeout:30];
area["name:en"="Sydney"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;