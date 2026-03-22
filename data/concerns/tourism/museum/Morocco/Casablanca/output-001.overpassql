[out:json][timeout:30];
area["name:en"="Casablanca"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;