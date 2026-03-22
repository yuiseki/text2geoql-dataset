[out:json][timeout:30];
area["name:en"="Ulsan"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;