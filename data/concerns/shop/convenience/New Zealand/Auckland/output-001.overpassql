[out:json][timeout:30];
area["name:en"="Auckland"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;