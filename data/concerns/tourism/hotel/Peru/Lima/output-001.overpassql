[out:json][timeout:30];
area["name:en"="Lima"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;