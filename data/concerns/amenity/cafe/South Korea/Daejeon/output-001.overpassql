[out:json][timeout:30];
area["name:en"="Daejeon"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;