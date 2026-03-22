[out:json][timeout:30];
area["name:en"="Mumbai"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;