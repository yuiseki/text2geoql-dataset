[out:json][timeout:30];
area["name:en"="Kaohsiung"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;