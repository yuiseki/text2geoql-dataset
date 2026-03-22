[out:json][timeout:30];
area["name:en"="Warsaw"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;