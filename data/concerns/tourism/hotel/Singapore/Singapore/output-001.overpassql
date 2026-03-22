[out:json][timeout:30];
area["name:en"="Singapore"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;