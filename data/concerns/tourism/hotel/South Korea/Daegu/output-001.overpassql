[out:json][timeout:30];
area["name:en"="Daegu"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;