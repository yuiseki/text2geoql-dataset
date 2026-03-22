[out:json][timeout:30];
area["name:en"="Toronto"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;