[out:json][timeout:30];
area["name:en"="Busan"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;