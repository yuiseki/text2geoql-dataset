[out:json][timeout:30];
area["name:en"="Daejeon"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;