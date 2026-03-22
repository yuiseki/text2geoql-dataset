[out:json][timeout:30];
area["name:en"="Daegu"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;