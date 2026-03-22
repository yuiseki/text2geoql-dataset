[out:json][timeout:30];
area["name:en"="Bucharest"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;