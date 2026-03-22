[out:json][timeout:30];
area["name:en"="Mumbai"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;