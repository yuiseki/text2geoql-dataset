[out:json][timeout:30];
area["name:en"="Lima"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;