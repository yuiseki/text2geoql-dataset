[out:json][timeout:30];
area["name:en"="Istanbul"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;