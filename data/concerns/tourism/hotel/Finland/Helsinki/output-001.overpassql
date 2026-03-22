[out:json][timeout:30];
area["name:en"="Helsinki"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;