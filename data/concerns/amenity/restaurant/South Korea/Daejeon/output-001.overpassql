[out:json][timeout:30];
area["name:en"="Daejeon"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;